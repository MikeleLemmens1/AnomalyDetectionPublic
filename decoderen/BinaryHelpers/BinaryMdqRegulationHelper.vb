Imports System.Collections.Specialized

Namespace Helpers
    Public Class BinaryMdqRegulationHelper
        Private itemIdBitSector As BitVector32.Section = BitVector32.CreateSection(63)
        Private value1BitSector As BitVector32.Section = BitVector32.CreateSection(7, itemIdBitSector)
        Private value2BitSector As BitVector32.Section = BitVector32.CreateSection(7, value1BitSector)
        Private value3BitSector As BitVector32.Section = BitVector32.CreateSection(7, value2BitSector)
        Private value4BitSector As BitVector32.Section = BitVector32.CreateSection(7, value3BitSector)
        Private value5BitSector As BitVector32.Section = BitVector32.CreateSection(7, value4BitSector)
        Private value6BitSector As BitVector32.Section = BitVector32.CreateSection(7, value5BitSector)

        Private Const BitVectorByteSize As Integer = 4
        Private Const NumberOfBytes As Integer = 8 'Defined in old CSO version as the number of bytes reserved for one item

#Region " Constructors "
        ''' <summary>
        ''' Instantiate a new BinaryMdqRegulationHelper
        ''' </summary>
        ''' <param name="mdqRegulationAnswers"></param>
        ''' <param name="itemIndex"></param>
        ''' <remarks>
        ''' The binary
        ''' Index |00000000|00111111|11112222|22222233|333333  
        '''       |01234567|89012345|67890123|45678901|234656...
        '''        item 1   item 2   item 3   item 4   item 5
        ''' The mdq answers byteArray consists of 400 bytes. This byteArray holds 30 items of each 8 bytes.
        ''' The 8 bytes are divided into two bitvectors of 32 bits. 
        ''' The first bitvector holds the normative values for the six statements, the second bitvector holds the six ipsative values.
        ''' Bitvector |0000000|000|111|111|111|122|222|2222233|
        '''           |0123456|789|012|345|678|901|234|5678901|
        '''           |Item Id| 1 | 2 | 3 | 4 | 5 | 6 |Unused
        ''' </remarks>
        Public Sub New(mdqRegulationAnswers As Byte(), itemIndex As Integer)
            Dim offSet As Integer = 0
            Dim itemBytes(NumberOfBytes - 1) As Byte

            'Get the bytes for the question index
            offSet = CInt((itemIndex - 1) / 2) * NumberOfBytes
            For byteIndex As Integer = 0 To NumberOfBytes - 1 'Get the bytes for one item
                itemBytes(byteIndex) = mdqRegulationAnswers(offSet + byteIndex)
            Next

            Dim normative As Integer = System.BitConverter.ToInt32(itemBytes, 0)

            Dim normativeBitVector As New BitVector32(normative)

            _ItemId = normativeBitVector(itemIdBitSector)
            _NormativeValues.Add(normativeBitVector(value1BitSector))
            _NormativeValues.Add(normativeBitVector(value2BitSector))
            _NormativeValues.Add(normativeBitVector(value3BitSector))
            _NormativeValues.Add(normativeBitVector(value4BitSector))
            _NormativeValues.Add(normativeBitVector(value5BitSector))
            _NormativeValues.Add(normativeBitVector(value6BitSector))
        End Sub
#End Region

#Region " Properties "
        Public Property ItemId As Integer
        Public Property NormativeValues As New List(Of Integer)
#End Region

#Region " Methods "
        ''' <summary>
        ''' Update answersbinary on item index
        ''' </summary>
        ''' <param name="answersBytes"></param>
        ''' <param name="itemIndex"></param>
        ''' <remarks>
        ''' The binary
        ''' Index |00000000|00111111|11112222|22222233|333333  
        '''       |01234567|89012345|67890123|45678901|234656...
        '''        item 1   item 2   item 3   item 4   item 5
        ''' The lsqAnswers byteArray consists of 400 bytes. This byteArray holds 30 items of each 8 bytes.
        ''' The 8 bytes are divided into two bitvectors of 32 bits. 
        ''' The first bitvector holds the normative values for the six statements, the second bitvector holds the six ipsative values.
        ''' Bitvector |0000000|000|111|111|111|122|222|2222233|
        '''           |0123456|789|012|345|678|901|234|5678901|
        '''           |Item Id| 1 | 2 | 3 | 4 | 5 | 6 |Unused
        ''' </remarks>
        Public Sub PutBinary(ByRef answersBytes As Byte(), itemIndex As Integer)
            Dim offSet As Integer = 0
            Dim itemBytes(NumberOfBytes - 1) As Byte '8 bytes

            'Get the bytes for the question index
            offSet = CInt((itemIndex - 1) / 2) * NumberOfBytes 'For some reason two bytes are skipped each time

            Dim normativeBitVector As New BitVector32(0)
            normativeBitVector(itemIdBitSector) = _ItemId
            normativeBitVector(value1BitSector) = _NormativeValues(0)
            normativeBitVector(value2BitSector) = _NormativeValues(1)
            normativeBitVector(value3BitSector) = _NormativeValues(2)
            normativeBitVector(value4BitSector) = _NormativeValues(3)
            normativeBitVector(value5BitSector) = _NormativeValues(4)
            normativeBitVector(value6BitSector) = _NormativeValues(5)

            Dim normativeBytes As Byte() = System.BitConverter.GetBytes(normativeBitVector.Data)

            For i As Integer = 0 To BitVectorByteSize - 1
                itemBytes(i) = normativeBytes(i)
            Next

            'Update the bytes for the question index
            For byteIndex As Integer = 0 To NumberOfBytes - 1
                answersBytes(offSet + byteIndex) = itemBytes(byteIndex)
            Next
        End Sub
#End Region

    End Class
End Namespace